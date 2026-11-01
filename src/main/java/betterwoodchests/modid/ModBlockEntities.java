package betterwoodchests.modid;

import net.fabricmc.fabric.api.object.builder.v1.block.entity.FabricBlockEntityTypeBuilder;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.Identifier;
import net.minecraft.world.level.block.entity.BlockEntityType;

public class ModBlockEntities {
    public static final BlockEntityType<WoodChestBlockEntity> WOOD_CHEST = Registry.register(
        BuiltInRegistries.BLOCK_ENTITY_TYPE,
        Identifier.fromNamespaceAndPath(BetterWoodChests.MOD_ID, "wood_chest"),
        FabricBlockEntityTypeBuilder.create(WoodChestBlockEntity::new, ModBlocks.chestArray()).build());

    public static void init() {}
}
