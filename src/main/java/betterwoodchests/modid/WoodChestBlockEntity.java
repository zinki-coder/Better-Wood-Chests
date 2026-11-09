package betterwoodchests.modid;

import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.world.level.block.ChestBlock;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.entity.ChestBlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.ChestType;

public class WoodChestBlockEntity extends ChestBlockEntity {
    public WoodChestBlockEntity(BlockPos pos, BlockState state) {
        this(ModBlockEntities.WOOD_CHEST, pos, state);
    }

    protected WoodChestBlockEntity(BlockEntityType<?> type, BlockPos pos, BlockState state) {
        super(type, pos, state);
    }

    @Override
    protected Component getDefaultName() {
        return getBlockState().getBlock().getName();
    }

    // Vanilla nimmt bei Doppeltruhen "Große Truhe", ausser eine Truhe hat einen Namen.
    @Override
    public boolean hasCustomName() {
        return true;
    }

    @Override
    public Component getDisplayName() {
        if (super.hasCustomName() || getBlockState().getValue(ChestBlock.TYPE) == ChestType.SINGLE) {
            return super.getDisplayName();
        }
        return Component.translatable("container.better-wood-chests.large", getBlockState().getBlock().getName());
    }
}
